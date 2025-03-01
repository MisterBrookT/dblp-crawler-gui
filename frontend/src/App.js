import React, { useState, useEffect } from 'react';
import { 
  Container, Box, Typography, TextField, Button, Paper, 
  Chip, FormControl, InputLabel, MenuItem, Select, 
  CircularProgress, Alert, Grid, Tabs, Tab, Divider,
  Table, TableBody, TableCell, TableContainer, TableHead, 
  TableRow, TablePagination, Checkbox, ListItemText, OutlinedInput
} from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import DownloadIcon from '@mui/icons-material/Download';
import SearchIcon from '@mui/icons-material/Search';
import axios from 'axios';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

const API_URL = 'http://localhost:8000';

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};

function App() {
  // Form state
  const [keywords, setKeywords] = useState('');
  const [conferences, setConferences] = useState([]);
  const [yearStart, setYearStart] = useState(2023);
  const [selectedCategories, setSelectedCategories] = useState([]);
  
  // Results state
  const [crawling, setCrawling] = useState(false);
  const [results, setResults] = useState([]);
  const [totalResults, setTotalResults] = useState(0);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [conferenceGroups, setConferenceGroups] = useState([]);
  const [tabValue, setTabValue] = useState(0);

  // Fetch conference groups when component mounts
  useEffect(() => {
    const fetchConferences = async () => {
      try {
        const response = await axios.get(`${API_URL}/conferences`);
        setConferenceGroups(response.data.categories || []);
      } catch (err) {
        console.error("Failed to fetch conferences:", err);
        setError("Failed to load conference data. Please check server connection.");
      }
    };

    fetchConferences();
  }, []);

  // Poll status when crawling
  useEffect(() => {
    let interval;
    
    if (crawling) {
      interval = setInterval(async () => {
        try {
          const response = await axios.get(`${API_URL}/status`);
          
          if (response.data.completed) {
            setCrawling(false);
            setSuccess(`Successfully crawled ${response.data.paper_count} papers.`);
            fetchResults();
          } else if (response.data.error) {
            setCrawling(false);
            setError(`Crawling failed: ${response.data.error}`);
          }
        } catch (err) {
          setCrawling(false);
          setError("Failed to check crawl status.");
        }
      }, 2000);
    }
    
    return () => clearInterval(interval);
  }, [crawling]);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleCategoryChange = (event) => {
    const selectedValues = event.target.value;
    setSelectedCategories(selectedValues);
    
    // Update conferences list based on all selected categories
    const newConferences = [];
    selectedValues.forEach(categoryName => {
      const group = conferenceGroups.find(g => g.name === categoryName);
      if (group && group.conferences) {
        group.conferences.forEach(conf => {
          // Only add if not already in the array
          if (!newConferences.includes(conf.value)) {
            newConferences.push(conf.value);
          }
        });
      }
    });
    
    setConferences(newConferences);
  };

  const handleRemoveConference = (confToRemove) => {
    setConferences(conferences.filter(conf => conf !== confToRemove));
  };

  const handleAddManualConference = (event) => {
    if (event.key === 'Enter' && event.target.value) {
      const newConf = event.target.value.trim().toLowerCase();
      if (newConf && !conferences.includes(newConf)) {
        setConferences([...conferences, newConf]);
        event.target.value = '';
      }
    }
  };

  const handleStartCrawl = async () => {
    // Validate input
    if (!keywords.trim()) {
      setError("Please enter at least one keyword");
      return;
    }
    
    if (conferences.length === 0) {
      setError("Please select at least one conference");
      return;
    }
    
    setError(null);
    setSuccess(null);
    setCrawling(true);
    
    try {
      const keywordsList = keywords.split(',').map(k => k.trim()).filter(k => k);
      
      await axios.post(`${API_URL}/crawl`, {
        keywords: keywordsList,
        confs: conferences,
        year_start: parseInt(yearStart)
      });
    } catch (err) {
      setCrawling(false);
      setError("Failed to start crawling. Please check server connection.");
    }
  };

  const fetchResults = async () => {
    try {
      const response = await axios.get(`${API_URL}/results`, {
        params: {
          limit: rowsPerPage,
          offset: page * rowsPerPage
        }
      });
      
      setResults(response.data.results || []);
      setTotalResults(response.data.total || 0);
      setTabValue(1); // Switch to results tab
    } catch (err) {
      console.error("Failed to fetch results:", err);
      setError("Failed to load results. Try downloading the CSV instead.");
    }
  };

  const handleDownload = () => {
    window.open(`${API_URL}/download`, '_blank');
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
    fetchResults();
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
    fetchResults();
  };

  // Find category name for a given conference value
  const getConferenceDisplayName = (confValue) => {
    for (const group of conferenceGroups) {
      const conf = group.conferences.find(c => c.value === confValue);
      if (conf) return conf.name;
    }
    return confValue.toUpperCase(); // Default fallback
  };

  return (
    <ThemeProvider theme={theme}>
      <Container maxWidth="md">
        <Box sx={{ my: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            DBLP Conference Paper Crawler
          </Typography>
          
          <Paper sx={{ p: 3, mb: 3 }}>
            <Tabs value={tabValue} onChange={handleTabChange}>
              <Tab label="Search" />
              <Tab label="Results" disabled={totalResults === 0 && !success} />
            </Tabs>
            
            <Box sx={{ mt: 3 }}>
              {tabValue === 0 ? (
                <Box>
                  <Grid container spacing={3}>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Keywords (comma separated)"
                        variant="outlined"
                        value={keywords}
                        onChange={(e) => setKeywords(e.target.value)}
                        disabled={crawling}
                        placeholder="e.g., machine learning, neural network"
                      />
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth variant="outlined">
                        <InputLabel id="category-select-label">Conference Categories</InputLabel>
                        <Select
                          labelId="category-select-label"
                          multiple
                          value={selectedCategories}
                          onChange={handleCategoryChange}
                          input={<OutlinedInput label="Conference Categories" />}
                          renderValue={(selected) => selected.join(', ')}
                          MenuProps={MenuProps}
                          disabled={crawling}
                        >
                          {conferenceGroups.map((group) => (
                            <MenuItem key={group.name} value={group.name}>
                              <Checkbox checked={selectedCategories.indexOf(group.name) > -1} />
                              <ListItemText primary={group.name} />
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        type="number"
                        label="Start Year"
                        variant="outlined"
                        value={yearStart}
                        onChange={(e) => setYearStart(e.target.value)}
                        disabled={crawling}
                      />
                    </Grid>
                  </Grid>
                  
                  <Box sx={{ mt: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="subtitle1">Selected Conferences:</Typography>
                      <TextField 
                        placeholder="Add custom conference..." 
                        size="small" 
                        onKeyPress={handleAddManualConference} 
                        disabled={crawling}
                      />
                    </Box>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, my: 1 }}>
                      {conferences.length > 0 ? (
                        conferences.map((conf) => (
                          <Chip
                            key={conf}
                            label={getConferenceDisplayName(conf)}
                            onDelete={crawling ? undefined : () => handleRemoveConference(conf)}
                          />
                        ))
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          No conferences selected
                        </Typography>
                      )}
                    </Box>
                  </Box>
                  
                  {error && (
                    <Alert severity="error" sx={{ mt: 2 }}>
                      {error}
                    </Alert>
                  )}
                  
                  {success && (
                    <Alert severity="success" sx={{ mt: 2 }}>
                      {success}
                    </Alert>
                  )}
                  
                  <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
                    <Button
                      variant="contained"
                      color="primary"
                      startIcon={crawling ? <CircularProgress size={20} color="inherit" /> : <SearchIcon />}
                      onClick={handleStartCrawl}
                      disabled={crawling}
                    >
                      {crawling ? 'Crawling...' : 'Start Crawling'}
                    </Button>
                    
                    {totalResults > 0 && (
                      <Button
                        variant="outlined"
                        startIcon={<DownloadIcon />}
                        onClick={handleDownload}
                      >
                        Download CSV
                      </Button>
                    )}
                  </Box>
                </Box>
              ) : (
                <Box>
                  <Box sx={{ mb: 2, display: 'flex', justifyContent: 'flex-end' }}>
                    <Button
                      variant="outlined"
                      startIcon={<DownloadIcon />}
                      onClick={handleDownload}
                    >
                      Download CSV
                    </Button>
                  </Box>
                  
                  <TableContainer>
                    <Table sx={{ minWidth: 650 }} aria-label="results table">
                      <TableHead>
                        <TableRow>
                          <TableCell>Title</TableCell>
                          <TableCell>Authors</TableCell>
                          <TableCell>Venue</TableCell>
                          <TableCell>Year</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {results.map((row, index) => (
                          <TableRow key={index}>
                            <TableCell>{row.title}</TableCell>
                            <TableCell>{row.authors}</TableCell>
                            <TableCell>{row.venue}</TableCell>
                            <TableCell>{row.year}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                  
                  <TablePagination
                    rowsPerPageOptions={[10, 25, 50]}
                    component="div"
                    count={totalResults}
                    rowsPerPage={rowsPerPage}
                    page={page}
                    onPageChange={handleChangePage}
                    onRowsPerPageChange={handleChangeRowsPerPage}
                  />
                </Box>
              )}
            </Box>
          </Paper>
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;
